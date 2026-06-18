# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_dbg.h

Purpose: compile-time and runtime debug macro controls for qla4xxx.

Important APIs/types: `DEBUG`, `DEBUG2`, `DEBUG2_3`, `DEBUG3`, `DEBUG4`, `DEBUG5`, `DEBUG7`, and `DEBUG9`. `QL_DEBUG_LEVEL_2` is enabled by default, but `DEBUG2` only emits when `ql4xextended_error_logging == 2`; `DEBUG2_3` emits unconditionally when level 2 is compiled.

Control flow: macros either execute the supplied statement block or compile to no-op depending on compile-time defines and runtime logging level.

State and persistence: no direct state except dependency on the external `ql4xextended_error_logging` variable. Logging persists in kernel logs.

Dependencies and integration: included by most qla4xxx files and wraps `ql4_printk`/`pr_info` diagnostics.

Risks: side effects inside disabled debug arguments will not run; enabled verbose levels can flood logs; `DEBUG2_3` being unconditional under level 2 means some messages are always compiled and executed. Test signals include builds with different debug defines and runtime extended logging value checks.
