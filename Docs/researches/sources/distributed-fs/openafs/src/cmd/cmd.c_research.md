# sources/distributed-fs/openafs/src/cmd/cmd.c

Purpose: command-line parsing framework for OpenAFS tools. It supports registering subcommands, aliases, parameter descriptors, hidden/implicit commands, help/apropos/version built-ins, abbreviated matching, positional parsing, quoted interactive-line parsing, and option lookup from config files.

Important APIs and types: public APIs include `cmd_CreateSyntax`, `cmd_CreateAlias`, `cmd_AddParm`, `cmd_AddParmAtOffset`, `cmd_AddParmAlias`, `cmd_Dispatch`, `cmd_Parse`, `cmd_FreeOptions`, `cmd_ParseLine`, `cmd_FreeArgv`, `cmd_DisablePositionalCommands`, `cmd_DisableAbbreviations`, `cmd_SetBeforeProc`, `cmd_SetAfterProc`, `cmd_OptionAsInt/Uint/String/List/Flag`, `cmd_OptionPresent`, `cmd_OpenConfigFile`, and raw config accessors. Global parser state includes `allSyntax`, `noOpcodes`, hook callbacks, abbreviation/positional toggles, `globalConfig`, and `commandName`.

Control flow: syntaxes are sorted alphabetically and receive an implicit `-help` parameter. On first parse, built-ins are registered. `cmd_Parse` resolves opcode or implicit `initcmd`, parses switches with optional `-x=value`, fills `cmd_item` lists, enforces required params, and returns a selected syntax. `cmd_Dispatch` handles built-ins before hooks, runs before/proc/after callbacks, and resets per-invocation option items. Config option helpers prefer command-line values, then `[command_subcommand]`, `[command]`, and `[defaults]`.

State and integration: parser definitions persist globally for process lifetime; parsed options are transient and freed after dispatch. Config parsing is supplied by the Heimdal-derived raw config layer compiled in the same library. Error returns are generated from `cmd_errors.et`.

Risks and tests: many allocations use `assert`, so allocation failure aborts instead of returning errors. Globals make independent parser contexts impossible. `cmd_ParseLine` has a fixed 256-byte token buffer and strips quotes without escape handling. Test programs cover opcode/no-opcode/interactive modes but not config fallback deeply.
