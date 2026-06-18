# sources/distributed-fs/ceph-client/tools/perf/tests/code-reading.c

Purpose: `code-reading.c` integration-tests perf's ability to read object code from mapped DSOs and compare it with `objdump` output for sampled instruction addresses.

Important APIs and state: a red-black tree of `tested_section` avoids retesting identical file/address sections. Objdump parsing helpers read hex bytes from disassembly lines and account for endian display. `read_object_code` resolves sample IPs to maps/DSOs, reads bytes through `dso__data_read_offset`, maps RIP to objdump address, and compares byte buffers. `do_test_code_reading` records a workload and processes samples.

Control flow: the test creates a live machine, loads kernel maps, optionally forces kallsyms for kcore testing, synthesizes thread maps, opens a suitable event from a fallback list, records a local workload that does file, sort, and syscall work, disables recording, and processes mmap events. Sample processing updates machine state for non-sample records and validates object-code reads for sample records. It tries normal and kcore paths and treats missing vmlinux/kcore/access as non-fatal skip-like success.

State and persistence: temporary workload files are removed. The test owns evlists, maps, machine, thread maps, CPU maps, and tested-section memory.

Dependencies, integration, risks, and tests: it depends on perf event access, symbol maps, DSO cache reads, objdump, kernel object availability, decompression for kernel modules, and architecture quirks such as RISC-V stop-address adjustment. Risks include environment sensitivity, objdump format changes, inaccurate kernel maps, and sampling nondeterminism. Test signals are matching byte buffers for sampled code sections or accepted no-access/no-kernel-object outcomes.
