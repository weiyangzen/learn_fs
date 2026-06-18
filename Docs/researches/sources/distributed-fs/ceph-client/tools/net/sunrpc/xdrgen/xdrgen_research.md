# sources/distributed-fs/ceph-client/tools/net/sunrpc/xdrgen/xdrgen

Purpose: Provides the command-line front end for the kernel XDR generator. It translates an XDR specification into Linux-kernel-oriented generated artifacts by dispatching to specialized subcommand modules.

Important APIs and state: `main()` builds an `argparse.ArgumentParser`, registers `definitions`, `declarations`, `lint`, and `source` subcommands, then calls the selected module's `subcmd(args)`. Shared options include `--annotate`, `--language`, `--peer`, and a positional XDR filename; `source` additionally exposes `--no-enum-validation`. The module-level `__version__` is used for `--version`.

Control flow: Startup resolves the script directory, prepends it to `sys.path` so sibling `subcmds` imports work, then also inserts the configured `@pythondir@` path. Runtime is a simple parse-and-dispatch path; `KeyboardInterrupt` and `BrokenPipeError` terminate with status 1.

Dependencies and integration: Depends on `subcmds.definitions`, `subcmds.declarations`, `subcmds.lint`, and `subcmds.source`. It is intended to be installed or configured by build tooling that substitutes `@pythondir@`.

State and persistence: No persistent state is written. The only state is parser configuration, import path mutation, and generated output produced by delegated subcommands.

Risks: The `--language` arguments use `action="store_true"` with default `"C"`, so passing the option stores boolean `True` rather than a language string unless subcommands account for that. Runtime depends on correct install-time substitution of `@pythondir@`. Import path insertion can mask similarly named modules.

Test signals: Exercise `--version`, each subcommand with a minimal XDR spec, missing filename handling, broken pipe behavior, both `--peer` values, annotated output, and `source --no-enum-validation`.
