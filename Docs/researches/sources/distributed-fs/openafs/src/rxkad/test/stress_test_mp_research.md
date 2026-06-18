# sources/distributed-fs/openafs/src/rxkad/test/stress_test_mp

Purpose: Shell helper for running repeated multi-process/threaded stress tests against rxkad.

Important flow: Defines loops and command aliases around `stm`/stress invocation, runs server and client combinations, and includes crypt-auth test invocations in the background.

State and persistence: Shell-only orchestration; process state is external to the script. It relies on the stress binary and environment rather than storing artifacts.

Dependencies and integration: Integrates with `stress`/`th_stress` test programs built by `Makefile.in`.

Risks: Background processes and timing make failures environment-sensitive. It is a manual/system stress helper rather than a deterministic unit test.

Test signals: Useful for repeated auth/crypt stress runs and multi-process behavior not covered by single TAP tests.
