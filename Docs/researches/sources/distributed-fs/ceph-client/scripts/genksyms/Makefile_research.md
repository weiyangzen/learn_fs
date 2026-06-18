# sources/distributed-fs/ceph-client/scripts/genksyms/Makefile

## Purpose
Defines the host-build rules for the `genksyms` tool that computes exported symbol ABI CRCs.

## APIs, Control Flow, and State
The Makefile adds `genksyms` to `hostprogs-always-y` and composes it from `genksyms.o`, generated parser object `parse.tab.o`, and generated lexer object `lex.lex.o`. It adds `-I $(src)` to parser and lexer host C flags so generated C files can include source-tree headers. It also declares that `lex.lex.o` depends on `parse.tab.h`, ensuring flex output sees bison token definitions before compilation.

## Dependencies and Integration
This integrates with kbuild host tools, bison/yacc-generated parser headers, flex-generated lexers, and the local `scripts/include` helpers. It has no runtime state.

## Risks and Test Signals
The key risk is stale generated lexer/parser ordering if dependencies are incorrect. Build success of `scripts/genksyms/genksyms`, correct regeneration after `parse.y` changes, and modversion build tests are the primary signals.
