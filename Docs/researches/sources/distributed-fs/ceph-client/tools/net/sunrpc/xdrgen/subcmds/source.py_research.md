# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/subcmds/source.py

Purpose: Implements the XDR generator subcommand that emits peer-specific C source files with XDR encoders and decoders.

Important APIs and functions: `emit_source_decoder` and `emit_source_encoder` dispatch one AST node to the correct generator. `generate_server_source` emits boilerplate, pass-through source blocks, decoders, then encoders. `generate_client_source` emits boilerplate, pass-through blocks, encoders, then decoders. `subcmd(args)` parses options and source.

Control flow: The command sets annotation and enum-validation modes, parses/transforms the XDR source, then switches on `args.peer`. Server output decodes RPC arguments and encodes results; client output encodes arguments and decodes results. Unsupported peers print a message but still return 0.

State and persistence behavior: Reads XDR input and writes C source text to stdout. It mutates global parser/AST side-channel state during parsing.

Dependencies and integration points: Complements generated declaration/definition headers and uses `XdrSourceTopGenerator` plus type/program generators.

Risks: Unsupported peer handling is not a hard error. Client procedure macro generation is marked TODO. Global state can leak across invocations. Pass-through is emitted before generated functions and can inject arbitrary C.

Test signals: Generate server and client source from the same RPC spec, with pass-through blocks, enum validation enabled/disabled, excluded procedures, and unsupported peer names.
