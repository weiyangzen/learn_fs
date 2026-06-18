# sources/distributed-fs/lizardfs/src/tools/tools_common_functions.cc

Purpose: Implements shared output formatting, path helpers, signal cancellation, and master connection helpers declared in `tools_common_functions.h`.

Important APIs/types/functions: Global `humode`, `eattrtab`, `eattrdesc`; `signalHandler`; `check_usage`; `set_humode`; `print_number`; `my_get_number`; basename/dirname helpers; connection functions are completed in `master_functions.cc`.

Control flow: `set_humode` reads `MFSHRFORMAT`. `print_number` prints fixed-width, IEC, or SI numbers and placeholder dashes. `signalHandler` waits for termination signals, opens a master connection, sends `cltoma::stopTask`, and prints cancellation outcome. Parsing/path functions support command implementations.

State and persistence: Maintains process-global output mode and static attribute name arrays. Signal handling opens transient master connections but stores no persistent state.

Dependencies and integration: Uses human-readable formatting, `mfserr`, `ServerConnection`, `cltoma`, `matocl`, socket helpers, and common path/system utilities. Long-running commands `snapshot` and `recursive_remove` use `signalHandler`.

Risks and test signals: Signal handling performs network operations after signals are routed through `sigwait`, so setup must block signals in calling threads. Global `humode` makes formatting process-wide. Numeric/path parsing edge cases can affect many commands. No direct tests in this subset.
