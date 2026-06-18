## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_uprobe_from_different_cu.sh

Purpose: verifies `perf probe` can find and add a uprobe for a function defined in a different compilation unit.
Important behavior: generates a header, `foo.c`, and `main.c`, compiles with debug info and LTO for `foo.o`, links an executable, lists functions matching `foo`, and adds a uprobe on `foo`.
Control flow: requires perf probe, root, and gcc; cleanup deletes the probe and temp build tree.
State and persistence: creates temporary source/object/binary files and a perf uprobe event on the generated binary.
Dependencies and integration: gcc debug info, LTO, perf probe CU lookup.
Risks: LTO/debug behavior can vary across compiler versions; cleanup must delete the probe before removing binary.
Test signals: `perf probe -x testfile --funcs foo` finds `foo` and `perf probe -x testfile foo` succeeds.
