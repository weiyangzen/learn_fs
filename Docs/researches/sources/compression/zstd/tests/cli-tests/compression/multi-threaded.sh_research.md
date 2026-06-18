# sources/compression/zstd/tests/cli-tests/compression/multi-threaded.sh

## Purpose
This test covers multi-threaded compression flags, rsyncable mode, automatic thread selection, job size configuration, and decompression warning behavior for explicit versus environment-sourced thread counts.

## APIs, control flow, and integration
Using `file` from setup, it runs compression with `--single-thread`, `-T2`, `--rsyncable`, `-T0`, `--auto-threads=logical`, `--auto-threads=physical`, and `--jobsize=1M`, testing each generated frame with `zstd -t`. It then compresses again and invokes decompression with explicit `-T0`, `-T2`, env `ZSTD_NBTHREADS=0/2`, and explicit `-T1` combinations to exercise warning/no-warning paths. The script relies on expectation files owned by the CLI harness for stderr matching.

## State, dependencies, risks, and test signals
Scratch outputs include `file.zst`, `file3`, and `file4`. Dependencies include multi-threading support in the binary and harness-provided stdout/stderr checks. Main risks are builds without thread support, platform CPU-count differences for `-T0`, and stderr wording churn. The functional signal is successful decompression; the behavioral signal is expected diagnostics under the runner.
