# sources/distributed-fs/ceph-client/tools/perf/perf-iostat.sh

### Purpose
`perf-iostat.sh` is a thin compatibility wrapper implementing `perf iostat` by delegating to `perf stat --iostat`.

### Important APIs, Types, And Functions
There are no functions. It chooses a delimiter and invokes `perf stat --iostat$DELIMITER$*`.

### Control Flow
If the first argument is `list` or looks like a PCI device selector (`hex:hex` optionally followed by comma), it uses `=` so the argument is attached as `--iostat=<value>`. Otherwise it uses a space, producing `--iostat <args>`.

### State And Persistence
No state is persisted; all behavior is delegated to `perf stat`.

### Dependencies And Integration Points
It depends on Bash regex matching and the installed `perf` executable. `perf.c` lists `iostat` as an external command (`fn == NULL`) so the dispatcher can run `perf-iostat`.

### Risks
Arguments are forwarded through `$*` unquoted, so whitespace-containing arguments are not preserved. Regex detection is simple and may misclassify unusual input.

### Test Signals
Run `perf iostat list`, `perf iostat <pci-selector>`, and normal interval/count forms, verifying the equivalent `perf stat --iostat` behavior.
