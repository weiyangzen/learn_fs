# `sources/distributed-fs/ceph-client/include/linux/if_phonet.h`

Purpose: tiny kernel Phonet interface header exposing header operations in addition to UAPI Phonet definitions.

Important APIs/types/functions: `phonet_header_ops` declaration.

Control flow and state: no inline logic or state; provides an integration symbol for Phonet netdevice setup.

Dependencies/integration: depends on UAPI `if_phonet.h` and `struct header_ops` from networking headers included by users.

Risks: very small surface; build failures mainly come from missing Phonet configuration or incorrect header-ops linkage.

Test signals: Phonet driver compile/link and netdevice setup path using `phonet_header_ops`.
