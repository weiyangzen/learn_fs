# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/prctl.c

Purpose: Beautifies `prctl(2)` option and selected option-dependent arguments.

Important APIs/types/functions: `syscall_arg__scnprintf_prctl_option` maps `PR_*` options and masks unused trailing arguments; `syscall_arg__scnprintf_prctl_arg2` formats `PR_SET_MM` suboptions and `PR_SET_NAME` pointers specially; `syscall_arg__scnprintf_prctl_arg3` formats `PR_SET_MM` addresses as hex.

Control flow: The option formatter looks up a sparse local mask table keyed by option value and ORs the relevant ignored-argument bits into `arg->mask`. The arg2/arg3 formatters inspect syscall argument 0 to choose context-sensitive rendering.

State and persistence: Only per-call display mask state is mutated.

Dependencies and integration points: Uses generated `prctl_option_array.c`, Linux `prctl.h`, and shared `strarray` helpers. Perf trace syscall definitions bind these functions to argument positions.

Risks: The mask table covers only selected options; unknown or complex options may show noisy unused arguments. Pointer contents are not copied for `PR_SET_NAME`, so it prints an address.

Test signals: Trace `PR_SET_NAME`, `PR_GET_DUMPABLE`, `PR_SET_MM`, and unknown options; verify masked argument behavior and prefix control.
