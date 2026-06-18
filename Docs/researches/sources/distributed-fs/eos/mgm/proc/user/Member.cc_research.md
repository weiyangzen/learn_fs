# sources/distributed-fs/eos/mgm/proc/user/Member.cc

Purpose: implements `ProcCommand::Member()`, a small inspection and refresh command for egroup membership.

Important APIs and types: reads `mgm.egroup` and `mgm.egroupupdate`, uses `gOFS->EgroupRefresh->refresh`, `DumpMember`, and `DumpMembers`, and references the caller through `vid.uid_string`.

Control flow: when a specific egroup is supplied, optional refresh is performed for the current user and that group, then the membership dump for that group is appended to stdout. Without a group, all known memberships are dumped.

State and persistence: optional refresh can update the egroup refresh subsystem's cache or backing state. Otherwise the command is read-only.

Dependencies and integration: depends on MGM egroup refresh services and virtual identity strings. It does not run the common path or token scope macros because it is not path based.

Risks: there is no explicit authorization barrier in this file; visibility is delegated to `EgroupRefresh`. Tests should verify refresh behavior, single-group and all-group output, empty group input, and error handling inside the egroup service.
