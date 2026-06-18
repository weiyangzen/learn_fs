# sources/distributed-fs/coda/coda-src/asr/asr.h

Purpose: Shared small header for the ASR resolver lexer/parser and rule implementation.

Important APIs/types: Defines lexer context constants `FILE_NAME_CTXT`, `DEP_CTXT`, `CMD_CTXT`, and `ARG_CTXT`; declares global `context` and `debug`; defines `DEBUG(a)` conditional logging macro.

Control flow and state model: The lexer changes tokenization based on `context`, and parser actions update that context as they move through object, dependency, command, and argument grammar regions.

Persistence and integration: No persistence. Included by resolver, lexer, parser, ruletypes, and path helper files.

Risks and test signals: Global mutable `context` and `debug` make the lexer/parser non-reentrant. The `DEBUG` macro lacks braces, so callers must use it carefully in control-flow contexts.
