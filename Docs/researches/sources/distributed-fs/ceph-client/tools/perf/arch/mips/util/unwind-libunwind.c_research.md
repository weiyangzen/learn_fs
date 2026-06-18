# sources/distributed-fs/ceph-client/tools/perf/arch/mips/util/unwind-libunwind.c

Purpose: Maps perf register numbers to libunwind architecture register IDs.

Important APIs/types/functions: `libunwind__arch_reg_id`.

Control flow: Switches over architecture perf register enum values and returns libunwind constants or `-EINVAL` for unsupported registers.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on libunwind target headers and perf register enums.

Risks: Mapping mistakes break callchain unwinding while compiling cleanly.

Test signals: Perf DWARF unwind tests and register mapping unit coverage.

Source coverage: researched from the complete local file (23 lines, 521 bytes).
