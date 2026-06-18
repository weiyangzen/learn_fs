# Research: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_debug.h

## Purpose

`mpt3sas_debug.h` centralizes logging bit definitions, conditional debug-print macros, and inline frame-dump helpers for the mpt3sas driver. It lets other mpt3sas files guard expensive or noisy diagnostics behind `ioc->logging_level` bits and provides standard dumps for MPI message frames, replies, and config pages.

## Important APIs, Types, And Macros

- Logging bits: `MPT_DEBUG`, `MPT_DEBUG_MSG_FRAME`, `MPT_DEBUG_SG`, `MPT_DEBUG_EVENTS`, `MPT_DEBUG_EVENT_WORK_TASK`, `MPT_DEBUG_INIT`, `MPT_DEBUG_EXIT`, `MPT_DEBUG_FAIL`, `MPT_DEBUG_TM`, `MPT_DEBUG_REPLY`, `MPT_DEBUG_HANDSHAKE`, `MPT_DEBUG_CONFIG`, `MPT_DEBUG_DL`, `MPT_DEBUG_RESET`, `MPT_DEBUG_SCSI`, `MPT_DEBUG_IOCTL`, `MPT_DEBUG_SAS`, `MPT_DEBUG_TRANSPORT`, `MPT_DEBUG_TASK_SET_FULL`, and `MPT_DEBUG_TRIGGER_DIAG`.
- Conditional macro core: `MPT_CHECK_LOGGING(IOC, CMD, BITS)` executes `CMD` only when `IOC->logging_level` contains the requested bit.
- Convenience wrappers: `dprintk`, `dsgprintk`, `devtprintk`, `dewtprintk`, `dinitprintk`, `dexitprintk`, `dfailprintk`, `dtmprintk`, `dreplyprintk`, `dhsprintk`, `dcprintk`, `ddlprintk`, `drsprintk`, `dsprintk`, `dctlprintk`, `dsasprintk`, `dmfprintk`, `dtsfprintk`, `dtransportprintk`, and `dTriggerDiagPrintk`.
- Dump helpers: `_debug_dump_mf()`, `_debug_dump_reply()`, and `_debug_dump_config()` interpret a buffer as little-endian dwords and print eight dwords per line with labels.

## Control Flow And Usage

Callers write debug code as a macro-wrapped command, for example `dctlprintk(ioc, ioc_info(...))`. At runtime the macro inspects `ioc->logging_level`; if the requested bit is not set, the command expression is not executed. The dump helpers are inline functions used when detailed frame/config visibility is needed. They loop over `sz` dwords, convert each with `le32_to_cpu()`, and emit the dump through `pr_info()`.

## State And Persistence Behavior

The header has no persistent state. It reads `IOC->logging_level`, which is maintained per adapter and is writable through the `logging_level` sysfs attribute implemented in `mpt3sas_ctl.c`. Logging choices persist only for the adapter lifetime or until changed by sysfs/module initialization.

## Dependencies And Integration Points

The macros assume `IOC` points to a `struct MPT3SAS_ADAPTER` with a `logging_level` field. The dump helpers require kernel logging and endian helpers. This header is included by mpt3sas implementation files that need debug gating; in this subset, `mpt3sas_ctl.c` uses `dctlprintk`, `dtmprintk`, and `_debug_dump_mf()` for ioctl/task-management diagnostics.

## Risks And Edge Cases

- Macro arguments can contain side effects; those side effects occur only when the logging bit is enabled.
- `MPT_CHECK_LOGGING` is a statement block macro, so callers must use it carefully in conditional contexts.
- `dsastransport` references `MPT_DEBUG_SAS_WIDE`, which is not defined in this header; it must be defined elsewhere or this macro is unsafe if used in a translation unit without that definition.
- Dump helpers trust the caller-provided size and pointer. Passing a short or invalid buffer can read beyond the intended frame.
- Excessive logging, especially frame dumps in hot paths, can flood kernel logs and perturb timing.

## Test Signals

Build coverage should compile all macro users and catch undefined logging bits such as `MPT_DEBUG_SAS_WIDE` if no external definition is present. Runtime tests can toggle the `logging_level` sysfs attribute and verify ioctl, task-management, config, reset, SCSI, and trigger diagnostics appear only for enabled bits. Fault-injection tests should avoid enabling broad frame dumps under high I/O load unless log-rate behavior is being explicitly evaluated.
