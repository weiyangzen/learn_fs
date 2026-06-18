# sources/distributed-fs/ceph-client/scripts/xen-hypercalls.sh

Purpose: `xen-hypercalls.sh` generates a list of Xen hypercall macro invocations from preprocessed hypercall definition headers.

Important APIs, types, and functions: it accepts an output path followed by input headers. For each input it runs `eval $CPP $LINUXINCLUDE -dD -imacros "$i" -x c /dev/null`, then awk collects `#define __HYPERVISOR_*` macros whose names match lowercase hypercall naming and maps numbers to names. The END block prints an auto-generated comment and `HYPERCALL(name)` lines for values without reverse duplicates, sorted uniquely.

Control flow: all inputs are preprocessed and concatenated into one awk pass; sorted output is redirected to the requested output file.

State and persistence: writes the generated output file.

Dependencies and integration points: depends on `CPP` and `LINUXINCLUDE` environment variables, Xen header macro naming, awk, and sort. Used by architecture Xen integration generation.

Risks: `eval` makes CPP/LINUXINCLUDE trusted build variables important. Macro parsing assumes `#define` field layout and numeric values in `$3`. Duplicate-value filtering is compact and should be tested when aliases exist.

Test signals: headers with unique hypercalls, aliases/duplicates, nonmatching uppercase names, and CPP include path failures.
