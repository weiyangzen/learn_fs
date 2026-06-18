<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spmi.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spmi.c

Purpose: Implements regmap access over SPMI base and extended register commands.

Important APIs/types/functions: Base command callbacks are `regmap_spmi_base_read()`, `regmap_spmi_base_gather_write()`, and `regmap_spmi_base_write()`. Extended callbacks are `regmap_spmi_ext_read()`, `regmap_spmi_ext_gather_write()`, and `regmap_spmi_ext_write()`. Exported init APIs are `__regmap_init_spmi_base()`, `__devm_regmap_init_spmi_base()`, `__regmap_init_spmi_ext()`, and `__devm_regmap_init_spmi_ext()`.

Control flow: Base reads require one-byte register buffers and perform repeated single-byte `spmi_register_read()` calls. Base writes optimize address zero through `spmi_register_zero_write()` then write remaining bytes one by one. Extended reads/writes require two-byte register buffers and split transfers: addresses up to `0xff` use 16-byte extended commands, higher addresses use long extended commands in 8-byte chunks. Plain write callbacks split the combined reg/value buffer into gather-write form.

State and persistence behavior: No private state or allocations exist. Register address increments are local variables per transfer.

Dependencies and integration points: Depends on SPMI core APIs and regmap raw callbacks. Native endian defaults are used for register/value formatting.

Risks: The code uses `BUG_ON()` for invalid reg sizes/counts rather than returning errors, relying on regmap core formatting to be correct. Address chunks are constrained by SPMI command limits. Pointer increments on `void *` use kernel C extensions.

Test signals: Validate base register-zero optimization, sequential base byte loops, extended short/long chunk splitting at `0xff`, error propagation mid-transfer, and core-provided register size assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spmi.c -->
