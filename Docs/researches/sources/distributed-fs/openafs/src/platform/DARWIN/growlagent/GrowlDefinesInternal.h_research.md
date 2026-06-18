# Research: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/GrowlDefinesInternal.h

Purpose: bundled Growl internal constants/types for network notification packets, plugin preferences, compatibility typedefs, and preference update macros.

Important APIs and state: defines fallback `NSInteger`, `NSUInteger`, and `CGFloat`, Growl network TCP/UDP ports, protocol versions, packet type constants, packed `GrowlNetworkPacket`, `GrowlNetworkRegistration`, and `GrowlNetworkNotification` structs, preference keys for Growl enabled/screenshot/app location/remote address, bundle identifiers and plugin extensions, and macros to synchronize/update/read/write Growl helper app preferences.

Control flow and persistence: preference macros read/write nested plugin settings inside the `com.Growl.GrowlHelperApp` preference domain and post `GrowlPreferencesChanged`. Packet structs define serialized network protocol layout.

Dependencies and integration: includes CoreFoundation, sys/types, and unistd. Used by Growl agent internals and plugin code compiled in this Darwin subtree.

Risks: packed bitfield layout in `GrowlNetworkNotificationFlags` is endian-sensitive. Preference macros rely on CoreFoundation ownership discipline and caller-provided domains/types. Legacy Growl ports and protocol versions may be incompatible with modern notification systems.

Test signals: struct sizes and byte order, registration/notification packet encode/decode, MD5/SHA256/no-auth type handling, preference read/write for bool/int/float/value, distributed preference update notification, and 32/64-bit CGFloat behavior.
