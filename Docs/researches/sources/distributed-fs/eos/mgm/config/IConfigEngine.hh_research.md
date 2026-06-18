## sources/distributed-fs/eos/mgm/config/IConfigEngine.hh

Purpose: declares the abstract interface and shared state for MGM configuration engines. It supports load/save/list/autosave implementations while centralizing apply, delete, publish, dump, and filter behavior.

Important APIs/types: `ICfgEngineChangelog` with `AddEntry()` and `Tail()` protected by `RWMutex`; `IConfigEngine` with static `ApplyEachConfig()` and `FormFullKey()`, pure virtual `LoadConfig()`, `SaveConfig()`, `ListConfigs()`, `AutoSave()`, `SetConfigValue()`, `DeleteConfigValue()`, `FilterConfig()`, and concrete `Get()`, `ApplyKeyDeletion()`, `DeleteConfigValueByMatch()`, `ApplyConfig()`, `DumpConfig()`, `ResetConfig()`, `SetAutoSave()`, `PublishConfigChange()`, and `PublishConfigDeletion()`.

State/integration: stores optional changelog, recursive mutex, autosave flag, current config name, and `sConfigDefinitions` map. Subclasses such as QuarkDB engines provide storage-specific behavior. Risks include broad access under `IN_TEST_HARNESS`, shared mutable definitions, and `FormFullKey()` treating null prefix differently from empty prefix. Tests should validate subclass contracts plus common apply/dump/get/delete helpers.
