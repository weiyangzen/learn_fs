<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/genl_magic_struct.h -->
# sources/distributed-fs/ceph-client/include/linux/genl_magic_struct.h

Purpose: Provides the declaration half of the generic-netlink macro generator: it requires family metadata macros, defines attribute helper macros, emits enums, compile-time uniqueness checks, generated structs, and signedness metadata.

Important APIs/types/functions: Requires `GENL_MAGIC_FAMILY`, `GENL_MAGIC_VERSION`, and `GENL_MAGIC_INCLUDE_FILE`. Declares generated register/unregister functions. Defines DRBD flags `DRBD_F_REQUIRED`, `DRBD_F_SENSITIVE`, and `DRBD_F_INVARIANT`. Field macros map logical fields to NLA types: flag, u8/u16/u32/s32/u64, string, and binary arrays. `GENL_doit()` and `GENL_dumpit()` add admin-permission ops. Macro passes generate operation enums, top-level attribute enums, nested attribute enums, `ct_assert_unique_*()` switch helpers, `struct s_name` declarations, and `F_*_IS_SIGNED` enums.

Control flow: Consumers provide a declarative include file. Multiple macro-expansion passes reinterpret the same declarations as enums, switch-case assertions, and structs.

State and persistence behavior: This header defines types and inline helpers only; no dynamic state. Generated structs hold parsed netlink payload values and array lengths.

Dependencies and integration points: Depends on Linux args/types and `<net/genetlink.h>`. It is paired with `genl_magic_func.h` for actual policies and conversion functions.

Risks: The macro DSL is fragile: missing required family macros stops compilation, and duplicate numbers are detected only through generated duplicate `case` labels if assertion functions compile. DRBD-specific semantics leak into all users.

Test signals: Build generated users with duplicate op/attribute numbers to verify compile failures, verify struct layout from field macros, string/binary length handling, signedness metadata, and operation flag generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/genl_magic_struct.h -->
