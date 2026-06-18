# sources/distributed-fs/ceph-client/drivers/virt/coco/tdx-guest/tdx-guest.c

## Purpose
Implements Intel TDX guest report, quote, and measurement-register interfaces.

## APIs, Types, and Functions
User API is a miscdevice named by `KBUILD_MODNAME` with ioctl `TDX_CMD_GET_REPORT0`. TSM report provider is `tdx_tsm_ops` using `tdx_report_new()`. Measurement support uses `tdx_mrs`, `tdx_measurements`, `tdx_mr_init()`, `tdx_mr_refresh()`, and `tdx_mr_extend()`. Quote helpers include `alloc_quote_buf()`, `free_quote_buf()`, `tdx_report_new_locked()`, and `wait_for_quote_completion()`.

## Control Flow and State
Initialization checks CPU feature `X86_FEATURE_TDX_GUEST`, initializes the TDREPORT buffer and measurement attribute group, registers the misc device, allocates a shared decrypted quote buffer, and registers TSM ops. `tdx_do_report()` serializes TDREPORT generation under `mr_lock`, copies optional reportdata, performs `tdx_mcall_get_report0()`, and copies the report out. TSM quote generation serializes under `quote_lock`, rejects in-flight buffers, embeds a TDREPORT in the quote buffer, invokes `tdx_hcall_get_quote()`, polls status for up to `getquote_timeout`, validates `out_len`, and copies quote data to `outblob`. RTMR extension reuses the aligned REPORTDATA area under the same MR lock.

## Dependencies and Integration
Depends on x86 TDX module calls, TDX hypercalls, memory encryption transitions for the shared quote buffer, miscdevice, shared TSM report frontend, and TSM measurement sysfs helpers.

## Risks and Test Signals
Risks include quote buffer leaks if decryption succeeds but later paths fail, in-flight quote ownership after timeout, shared `tdx_report_buf` reuse between report and RTMR extension, and MR offset-to-pointer patching. Tests should cover feature absence, ioctl report generation, TSM quote timeout and oversized output, interruptible locks, RTMR extension serialization, measurement sysfs reads/writes, and encryption restoration on module exit.
