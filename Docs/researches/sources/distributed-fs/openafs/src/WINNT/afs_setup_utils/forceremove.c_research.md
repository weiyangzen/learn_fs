# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/forceremove.c

Purpose: forcibly removes a legacy AFS 3.4a Windows client when normal InstallShield uninstall is unavailable or incomplete.

Important APIs/types/functions: exported `Client34Eradicate(BOOL keepConfig)` orchestrates removal. Helpers include `ClientSoftwareGet()` for install version/path registry discovery, `ClientServiceDelete()` for SCM stop/delete, `DirectoryForceRemove()` for recursive deletion, `FileForceRemove()` for immediate or reboot-delayed deletion, `FolderLocateInTree()` for start-menu cleanup, and `Client34ZapUninstallKeys()` for Microsoft uninstall key cleanup.

Control flow: the main routine detects installed client version and exits if a newer client exists. It stops/deletes the client service, removes install directories and known log/control-panel/shell-extension files, optionally removes config files, repeatedly finds and removes "Transarc AFS Client" folders, deletes legacy registry values/keys, removes the client from network provider order, and removes its program directory from PATH.

State/persistence: no durable internal state. Persistent effects are deletion or delayed deletion of files/directories, service removal, registry mutation, PATH mutation, and provider-order mutation.

Dependencies/integration: depends on OpenAFS `afsreg` registry helpers, `sutil` PATH/provider helpers, Windows filesystem/SCM APIs, and legacy registry key names.

Risks/test signals: path buffers use `sprintf()` into `MAX_PATH`, removal is intentionally destructive, and partial failures are accumulated while cleanup continues. Tests should run in a disposable Windows fixture and cover missing registry info, newer version no-op, in-use file delayed deletion, same-drive temp fallback, service absent/active/marked-for-delete cases, uninstall-key enumeration, and `keepConfig` behavior.
