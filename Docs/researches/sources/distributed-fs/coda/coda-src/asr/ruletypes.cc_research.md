# sources/distributed-fs/coda/coda-src/asr/ruletypes.cc

Purpose: Implements ASR rule language runtime objects: object-name matching, dependency records, command argument expansion, command execution, repair-mode interaction, and rule execution.

Important APIs/classes/functions: `objname_t`, `depname_t`, `arg_t`, `command_t`, `rule_t`, and `expandstring`. Key methods include `match`, `GetPrefix`, `expandname`, `expandreplicas`, `execute`, `GetReplicaNames`, `enablerepair`, `disablerepair`, `GetRepInfo`, and print helpers.

Control flow: Object names are split into directory/file and matched with `wildmat`; leading `*` rules derive a prefix for `$*`. Matching a rule records inconsistent directory/name, attempts to identify inconsistent symlink metadata, and exposes replica names by temporarily enabling repair and reading child entries. Rule expansion substitutes `$*`, `$<`, `$>`, `$#`, and replica selectors, expanding `[all]` into multiple arguments. Commands fork and `execv` the configured executable, waiting for completion and stopping on first nonzero status.

State and persistence: Rule objects hold parsed lists, replica names, Coda FID metadata, and conflict path state. Persistent effects are indirect: `pioctl` toggles Venus repair mode and executed commands can mutate the filesystem.

Dependencies and integration: Depends on `olist`, `inconsist`, `venusioctl`, `vcrcommon`, `path`, `wildmat`, and Coda repair ioctls. Invoked by `resolver.cc` after parsing.

Risks and test signals: Many string expansions use fixed `MAXPATHLEN` buffers, `sprintf`, `strcpy`, and `strcat` without robust bounds checks. `command_t::execute` only supports absolute/relative executable paths as parsed; no shell is used here, but rule-controlled commands still execute with resolver privileges. `GetReplicaNames` relies on temporary repair mode and directory listing order. `expandstring` assumes the final string fits.
