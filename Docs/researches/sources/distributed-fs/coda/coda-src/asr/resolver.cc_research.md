# sources/distributed-fs/coda/coda-src/asr/resolver.cc

Purpose: Main program for the older application-specific resolver (`parser`) that reads a `RESOLVE` file, matches a rule to an inconsistent object, enables Coda repair mode, executes rule commands, and disables repair mode.

Important APIs/functions: `IsAbsPath`, `FindResolveFile`, `FindRule`, `ParseArgs`, and `main`. Global state includes `cwd` and `olist rules`, populated by yacc parsing.

Control flow: Arguments accept optional `-d` and an inconsistent filename. Relative paths are made absolute from `getcwd`, then split into directory/name. `FindResolveFile` searches upward from the inconsistent directory until `/coda`, looking for `RESOLVE`. `yyparse` populates rule objects. `FindRule` calls each rule's `match` and `expand`. If a rule matches, main enables repair, executes commands sequentially, and disables repair.

State and persistence: Runtime state is in global rule lists and the Coda kernel/Venus repair state manipulated by `pioctl` through `rule_t`. It reads a filesystem `RESOLVE` file but does not write persistent files.

Dependencies and integration: Depends on flex/bison outputs, `ruletypes`, `path`, `wildmat`, Coda ioctl definitions, `olist`, and Coda repair interfaces.

Risks and test signals: Path construction uses fixed buffers and unbounded `strcat`/`strcpy`. `FindResolveFile` assumes `/coda` as root sentinel. Repair disable is best-effort after command execution; failures before disable can leave state dependent on Venus cleanup. Parser behavior is tested only by building/running the client and sample `resolve.eg`.
