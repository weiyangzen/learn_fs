# sources/distributed-fs/ceph-client/tools/verification/rvgen/dot2c

Purpose: `dot2c` is a small executable wrapper that converts a DOT automaton into a C automaton model printed on stdout.

Important flow: it imports `rvgen.dot2c`, parses one positional `dot_file`, instantiates `Dot2c`, and calls `print_model_classic()`.

Control flow and integration: unlike `rvgen monitor`, it does not generate a full kernel monitor scaffold. It is useful for inspecting or embedding just the deterministic/hybrid automaton C representation produced from DOT.

State and dependencies: no persistent state is written by this script. It depends on Python 3, the installed/importable `rvgen` package, and a valid DOT file accepted by `Automata`. Risks include uncaught `AutomataError` tracebacks in this wrapper and stdout-only output without file selection. Test signals are `dot2c model.dot` producing enum definitions, transition matrix, and automaton initializer.
