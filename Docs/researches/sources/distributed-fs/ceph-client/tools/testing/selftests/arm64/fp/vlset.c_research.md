<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/vlset.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/vlset.c

Purpose: command wrapper that sets SVE or SME vector length for the next exec, then executes a requested command.

Important APIs and functions: `parse_options` handles `--force`, `--inherit`, `--no-inherit`, `--max`, `--sme`, and help. `main` validates VL, checks SVE HWCAP unless forced, calls `prctl(PR_SVE_SET_VL or PR_SME_SET_VL, vl | PR_SVE_SET_VL_ONEXEC | optional INHERIT)`, reads back current flags with `PR_*_GET_VL`, and `execvp`s the command.

Control flow: parse options and VL, reject invalid/missing command, optionally continue without SVE under `--force`, set on-exec VL, verify prctl get succeeds, then exec. Return codes follow shell conventions: 2 for usage, 126 for not executable, 127 for not found.

State and persistence: only process-local prctl state that affects the execed child. No files.

Dependencies and integration: helper utility for running tests/programs at specific SVE/SME VLs.

Risks: HWCAP check only tests SVE even when `--sme` is requested. The VL validation expression `vl & ~(vl & PR_SVE_VL_LEN_MASK)` is suspicious and may not implement the intended mask rejection. `--no-inherit` is parsed but not actively used beyond conflict detection.

Test signals: stderr explains usage, missing feature, prctl, or exec failures; success replaces the process image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/vlset.c -->
