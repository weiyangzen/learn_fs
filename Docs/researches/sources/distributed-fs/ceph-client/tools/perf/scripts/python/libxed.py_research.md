# sources/distributed-fs/ceph-client/tools/perf/scripts/python/libxed.py

Purpose: `libxed.py` is a minimal ctypes wrapper around Intel XED for perf Python scripts that want x86 instruction disassembly without embedding XED bindings in perf itself.

Important APIs and types: `xed_state_t` mirrors the XED machine-mode state passed to `xed_operand_values_set_mode`. `XEDInstruction` owns a fixed-size decoded-instruction buffer, mode state, and output text buffer. `LibXED` loads `libxed.so`, binds the XED entry points, initializes tables, and exposes `Instruction`, `SetMode`, and `DisassembleOne`.

Control flow: `LibXED.__init__` first tries the dynamic linker path and then `/usr/local/lib/libxed.so`, assigns return and argument types for the used functions, and calls `xed_tables_init`. Callers allocate an `XEDInstruction`, set 32-bit or 64-bit mode, and pass bytes plus an IP to `DisassembleOne`. That method clears the decoded instruction while preserving mode, decodes bytes, formats AT&T syntax, decodes the output buffer for Python 3, and returns an instruction length plus text.

State and dependencies: all state is per-wrapper or per-instruction object. There is no persistent file output. The dependency is a compatible `libxed.so` ABI with symbols and layout matching this wrapper.

Integration, risks, and tests: `intel-pt-events.py` uses this helper opportunistically. The largest risk is ABI drift: decoded instruction length is read from hard-coded byte `166` in a 512-byte scratch buffer, so a future XED layout could return wrong lengths while still loading. Test signals are successful import, library load, and known-byte disassembly in instruction trace mode.
