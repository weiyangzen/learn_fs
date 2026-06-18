<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssbi.h -->
# sources/distributed-fs/ceph-client/include/linux/ssbi.h

Purpose: Declares SSBI read/write accessors and adapts them to regmap-style single-register callbacks.

Important APIs/types/functions: `ssbi_write()`, `ssbi_read()`, `ssbi_reg_read()`, and `ssbi_reg_write()`.

Control flow: `ssbi_reg_read()` reads one byte through `ssbi_read()` and stores it into an `unsigned int` on success. `ssbi_reg_write()` truncates the value to one byte and writes it through `ssbi_write()`.

State and persistence behavior: No state in the header. Operations affect device registers behind the provided device/context pointer.

Dependencies: `linux/types.h`; uses `struct device` through declarations.

Integration points: Qualcomm/Android-era SSBI bus devices and regmap adapters.

Risks: Register helper callbacks are byte-wide; callers must not expect multi-byte regmap semantics. `void *context` is treated as the device pointer expected by `ssbi_read/write`.

Test signals: Bus read/write transaction tests, regmap single-byte callback tests, error propagation tests, and value truncation coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssbi.h -->
