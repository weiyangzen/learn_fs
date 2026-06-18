## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_coresight_disasm.sh

Purpose: validates the Arm CoreSight Python disassembly script can reconstruct and disassemble trace ranges without errors.
Important behavior: skips without `cs_etm//`, records kernel trace with `--kcore` when `/proc/kcore` exists, always records userspace trace, and runs `arm-cs-trace-disasm.py -d --stop-sample=30`.
Control flow: checks script output for likely branch instructions (`bl`, `b`, conditional branches, `cbz`).
State and persistence: temp perf.data directory and output temp file are cleaned, with `glb_err` defaulting to failure until all checks pass.
Dependencies and integration: CoreSight decode, Python script path, objdump behavior, `/proc/kcore` for kernel decode.
Risks: branch mnemonic regex is heuristic; kernel test skips when kcore is unavailable.
Test signals: branch instruction text found in disassembly output.
