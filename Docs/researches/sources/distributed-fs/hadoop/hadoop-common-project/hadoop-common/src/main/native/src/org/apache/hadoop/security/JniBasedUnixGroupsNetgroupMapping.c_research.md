# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/security/JniBasedUnixGroupsNetgroupMapping.c

## Purpose
`JniBasedUnixGroupsNetgroupMapping.c` implements the native JNI method behind `JniBasedUnixGroupsNetgroupMapping.getUsersForNetgroupJNI`. It resolves a Unix netgroup name into the users listed by the platform netgroup database and returns them to Java as a `String[]`.

## Important APIs, types, and functions
The only exported JNI symbol is `Java_org_apache_hadoop_security_JniBasedUnixGroupsNetgroupMapping_getUsersForNetgroupJNI`. Internally it uses a small `UserList` singly linked list to stage user names before the final Java array is allocated. Platform APIs are `setnetgrent`, `getnetgrent`, and `endnetgrent`; JNI APIs include `GetStringUTFChars`, `NewObjectArray`, `FindClass`, `NewStringUTF`, and `SetObjectArrayElement`. Exceptions are raised through Hadoop's `THROW` macro from `org_apache_hadoop.h`.

## Control flow
The method converts the Java netgroup name into a UTF-8 C string, opens netgroup iteration, walks every `(host,user,domain)` tuple, copies non-null user entries into the linked list, allocates a Java `String` array sized to the collected count, and fills it from the list. A single `END` cleanup path releases the Java string, calls `endnetgrent` if lookup was started, frees all list nodes, and either returns the array or throws the selected Java exception.

## State and persistence
All state is per-call native heap and libc netgroup iterator state. There is no persistent Hadoop state. The returned array order is reverse iteration order because new list nodes are pushed at the head.

## Dependencies and integration points
This file integrates Java group mapping with OS netgroup sources such as `/etc/netgroup`, NIS, or LDAP as exposed by libc. It is compiled into the Hadoop native library and called by `JniBasedUnixGroupsNetgroupMapping` and its fallback wrapper when native code is available.

## Risks and test signals
Risks include platform differences in `setnetgrent` return values, Linux treating an unknown netgroup as an `IOException`, unchecked `malloc` failures for list nodes and strings, duplicate user entries, and reverse-order results. Test signals include unknown netgroup behavior on Linux and BSD/macOS, netgroups with null user fields, large member lists, OOM/fault injection around JNI string allocation, and fallback behavior when the native library is absent.
