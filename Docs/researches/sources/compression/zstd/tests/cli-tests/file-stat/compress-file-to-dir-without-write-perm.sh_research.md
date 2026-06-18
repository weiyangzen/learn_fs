# sources/compression/zstd/tests/cli-tests/file-stat/compress-file-to-dir-without-write-perm.sh

## Purpose
This regression test, motivated by issue 3523, exercises file-stat tracing when output targets a directory without write permission.

## APIs, control flow, and integration
It generates `file`, creates `out`, applies `chmod 000 out`, runs `zstd file -q --trace-file-stat -o out/file.zst`, tests `out/file.zst`, and restores permissions with `chmod 777 out`. The expected behavior depends on the test environment permissions; under some privileged users, writes can still succeed.

## State, dependencies, risks, and test signals
State includes `file`, `out/`, and `out/file.zst`. The test depends on permission semantics and `--trace-file-stat` instrumentation. The major risk is running as root or on filesystems that ignore mode bits, which can change the intended coverage. A pass indicates the trace path does not break compression/output validation in this scenario.
