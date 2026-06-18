# sources/distributed-fs/ceph-client/tools/include/linux/btf_ids.h

## Purpose

This header defines structures and macros for representing BTF ID sets in kernel-derived tools code.

## APIs, State, and Dependencies

It defines `struct btf_id_set` and `struct btf_id_set8`. When `CONFIG_DEBUG_INFO_BTF` is enabled, macros such as `BTF_ID`, `BTF_ID_LIST`, `BTF_SET_START`, and `BTF_SET_END` emit zero-filled records into the `.BTF_ids` section for later resolution by `resolve_btfids`. When disabled, the macros become static placeholder objects or no-ops. It also enumerates socket and tracing BTF type categories and declares related ID arrays.

## Risks and Test Signals

The assembly layout must match `resolve_btfids` expectations. Disabled-BTF fallbacks must still satisfy references without section data. Tests should build with and without `CONFIG_DEBUG_INFO_BTF`, inspect `.BTF_ids` layout, and run the resolver on users that define BTF sets.
