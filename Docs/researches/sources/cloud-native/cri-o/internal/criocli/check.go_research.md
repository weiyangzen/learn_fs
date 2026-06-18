# sources/cloud-native/cri-o/internal/criocli/check.go

Purpose: implements `crio check`, a storage integrity checker and optional repair/wipe tool for CRI-O storage.

Important APIs/types/functions: `checkErrors` alias, `CheckCommand`, `crioCheck`, and the long `usageText`. Flags include `age`, `force`, `repair`, `quick`, and `wipe`.

Control flow: `crioCheck` loads config, opens the storage store, defers shutdown, builds `storage.CheckOptions` using either `CheckEverything` or `CheckMost`, parses maximum unreferenced-layer age, runs `store.Check`, logs detailed report entries, and determines whether errors exist. Without `--repair`, any errors produce a summarized error. With repair, it calls `store.Repair`, optionally removes the whole storage directory on repair failure when `--wipe` is set, and returns remaining read-only/container errors according to `--force`.

State and persistence behavior: reads and may mutate container storage when repair or wipe is requested. It can remove damaged containers when forced and can remove the storage directory through `lib.RemoveStorageDirectory`.

Dependencies/integration points: urfave/cli, logrus, containers/storage, CRI-O `lib`, config loading, and duration parsing utilities.

Risks: repair/wipe operations are destructive and assume CRI-O and containers are stopped. Quick check intentionally differs from startup quick repair behavior. Error summaries use counts by report map size, not total nested errors.

Test signals: no direct tests in this subset for `crio check`.
