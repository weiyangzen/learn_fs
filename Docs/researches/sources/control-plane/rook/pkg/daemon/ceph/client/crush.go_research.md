# sources/control-plane/rook/pkg/daemon/ceph/client/crush.go

Purpose: provides command wrappers and helpers for reading, modifying, compiling, and injecting Ceph CRUSH map information.

Important APIs/types: `CrushMap` models devices, types, buckets, rules, and tunables from `ceph osd crush dump`. `ruleSpec` and `stepSpec` model CRUSH rule JSON used by `crush_rule.go`. `CrushFindResult` models `ceph osd find`. Public helpers include `GetCrushMap()`, `GetCompiledCrushMap()`, `FindOSDInCrushMap()`, `GetCrushHostName()`, `NormalizeCrushName()`, `GetCrushRootFromSpec()`, `IsNormalizedCrushNameEqual()`, `UpdateCrushMapValue()`, and `GetOSDOnHost()`. Package helpers compile/decompile/inject/set CRUSH maps and construct derived file names.

Control flow and state: `GetCrushMap()` and `FindOSDInCrushMap()` run Ceph commands and unmarshal JSON. `GetCompiledCrushMap()` creates a temp file and asks Ceph to write the compiled map into it, returning the file path; cleanup is left to callers. `compileCRUSHMap()` and `decompileCRUSHMap()` run local `crushtool` and write sibling `.compiled`/`.decompiled` files. `injectCRUSHMap()` and `setCRUSHMap()` mutate cluster CRUSH state through Ceph commands with plain output.

Dependencies and integration: used by pool/stretch-cluster logic and OSD placement management. It integrates with `cephv1.ClusterSpec` storage config and command execution. Risks include uncleaned temp files, unsafe `UpdateCrushMapValue()` parsing on malformed `key=value` entries, map-order nondeterminism from Ceph output, and direct cluster mutation in inject/set helpers. Tests cover JSON dump parsing, host OSD listing, name normalization, and file-name helpers; command failure paths and temp file cleanup are not covered.
