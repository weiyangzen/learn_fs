# sources/distributed-fs/ceph-client/include/uapi/linux/keyctl.h

## Purpose
`keyctl.h` defines operation codes, special keyring IDs, default request-key destinations, crypto parameter structures, public-key operation structures, move flags, and capability bits for the Linux key retention service.

## Important APIs, Types, and Functions
Special IDs address thread, process, session, user, user-session, group, request-key auth, and requestor keyrings. `KEYCTL_*` opcodes cover keyring lookup/join, update, revoke, chown, permissions, describe, clear, link/unlink/search/read, instantiate/negate/reject, timeout, authority, security label, parent session migration, persistent keyrings, Diffie-Hellman, public-key query/encrypt/decrypt/sign/verify, restriction, move, capabilities, and watch. Structures include `keyctl_dh_params`, `keyctl_kdf_params`, `keyctl_pkey_query`, and `keyctl_pkey_params`.

## Control Flow
Userspace calls the `keyctl` syscall with an opcode and operation-specific arguments. The kernel resolves key IDs or special keyrings, checks permissions and namespaces, then mutates key/keyring state or performs crypto operations.

## State and Persistence
Keys and keyrings are kernel objects with ownership, permissions, expiry, revocation, links, quotas, and namespace/user associations. Persistent keyrings can survive login sessions according to kernel policy.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Integration points include request-key upcalls, fscrypto, network filesystems, module verification, public-key crypto, watch queues, user namespaces, and security labels.

## Risks and Test Signals
Tests should cover permission bits, special keyring resolution, quota/expiry/revocation, instantiate authorization, move exclusivity, capability bitmap length, watch notifications, and crypto buffer sizing. Security risk is high because the ABI controls credentials and secret material.
