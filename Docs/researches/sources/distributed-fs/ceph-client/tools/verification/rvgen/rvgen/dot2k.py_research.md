# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/dot2k.py

Purpose: `dot2k.py` converts DOT deterministic (`da`) or hybrid (`ha`) automata into kernel RV monitor scaffolds.

Important classes and methods: `dot2k` inherits from `Monitor` and `Dot2c`, combines templates with automaton data, sets enum suffixes, and emits tracepoint handler skeletons, attach/detach stubs, model headers, tracepoint prototypes, monitor class type, and main C replacements. `da2k` rejects hybrid automata. `ha2k` requires hybrid automata, switches to hybrid trace templates, parses constraints into guards/invariants, emits env getter/resetter stubs, timer setup, invariant verification, guard verification, invariant/guard conversion, and hybrid constraint verification.

Control flow and integration: top-level `rvgen monitor -c da|ha` constructs these classes and writes monitor files. Generated code still contains `XXX` tracepoint and environment placeholders that developers must fill.

State and dependencies: state includes parsed automaton, monitor type (`global`, `per_cpu`, `per_task`, `per_obj`), parent/container, and templates. Dependencies are DOT label conventions, kernel RV DA/HA monitor APIs, and template placeholders. Risks include heavy f-string code generation requiring Python versions supporting the syntax, fragile string-based constraint parsing, multiple-inheritance initialization ordering, no validation that generated handler names are valid C, and subtle HA timer semantics if resets/invariants are modeled incorrectly. Test signals are generated scaffolds compiling after filling `XXX` hooks, expected errors when DA/HA class mismatches the spec, and unit examples covering guard, reset, invariant, stored env, and timer conversions.
