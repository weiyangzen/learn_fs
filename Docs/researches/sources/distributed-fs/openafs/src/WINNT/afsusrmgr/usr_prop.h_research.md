# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_prop.h

Purpose: defines the user property-sheet public model and constants.

Important APIs/types: constants define ticket lifetime, group quota, password-expiration, and quota boundaries. `USERPROPTAB` names selectable tabs. `USERPROPINFO` is the central state structure for property editing: target user list, modal/modeless behavior, machine flag, apply flags, general password/expiration/lockout fields, advanced KAS/PTS fields, ACL access values, mixed-state flags, and membership/ownership ASID lists. Exports are `User_ShowProperties` overloads and `User_FreeProperties`.

State and dependencies: the structure bridges create dialogs, property sheets, and task payload generation. It stores pending user edits but no durable data itself.

Risks and test signals: this header is a cross-module contract; adding fields requires updating initialization, copy, apply, and free paths. Tests should cover default initialization, modal create-mode behavior, mixed-state preservation, and ASID-list ownership.
