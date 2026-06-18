# sources/distributed-fs/ceph-client/security/apparmor/include/af_unix.h

## Purpose
This header declares the AF_UNIX AppArmor mediation API and small classification macros for Unix socket addresses and socket state. It connects LSM socket hooks and file revalidation code to `af_unix.c`.

## Important APIs and types
The header declares `aa_sunaddr`, `aa_unix_create_perm`, `aa_unix_bind_perm`, `aa_unix_connect_perm`, `aa_unix_listen_perm`, `aa_unix_accept_perm`, `aa_unix_msg_perm`, `aa_unix_opt_perm`, `aa_unix_sock_perm`, `aa_unix_peer_perm`, and `aa_unix_file_perm`. Macros classify abstract, anonymous, filesystem-backed, connected, and peer sockets.

## Control flow and integration
Callers use these prototypes from socket LSM hooks and `file.c` open-file revalidation. Filesystem-vs-abstract address macros determine whether mediation goes through path rules or network DFA rules.

## State and dependencies
It depends on `net/af_unix.h` and AppArmor labels. It does not define state; it exposes access to Unix socket internals through macros.

## Risks
The macro guard is written as `#ifndef __AA_AF_UNIX_H` without a visible `#define`, so repeated inclusion relies on surrounding include behavior and could be fragile. The macros directly dereference Unix socket internals and must only be used with valid socket state and appropriate locks/RCU context.

## Test signals
Compile all users with warnings enabled, especially repeated includes. Exercise address classification for abstract, anonymous, autobind, and filesystem sockets.
