# sources/distributed-fs/coda/coda-src/al/pdbtool.c

Purpose: Interactive and one-shot command-line administration tool for the protection database.

Important APIs/functions: Command handlers include `tool_byNameOrId`, `tool_list`, `tool_newUser`, `tool_newUser_Id`, `tool_changeName`, `tool_newGroup`, `tool_newDefGroup`, `tool_lookup`, `tool_clone`, `tool_addtoGroup`, `tool_removefromGroup`, `tool_delete`, `tool_update`, `tool_compact`, `tool_get_maxids`, `tool_maxids`, `tool_changeId`, `tool_ldif_export`, `tool_export`, `tool_import`, `tool_source`, and `tool_help`. `pdbcmds` registers these with the parser.

Control flow: Startup reads `server.conf`, initializes `vice_dir`, ensures the database exists, initializes the command parser, and either enters an interactive prompt or concatenates argv into one command line. Handlers parse names/IDs, validate existence, call high-level PDB mutations, and print status. Export paths dump passwd/group-like or LDIF data; import recreates users, then groups, then group memberships in multiple passes.

State and persistence: Mutates `db/prot_users.cdb` via PDB APIs. Import/export also read/write user-specified flat files. `tool_compact` runs historical bug fixups before calling the currently-stubbed compact routine.

Dependencies and integration: Depends on parser utilities, `codaconf`, `vice_file`, `pdb.h`, and the AL/PDB stack. It is the operator-facing bridge for PDB maintenance and migration.

Risks and test signals: The tool uses fixed buffers and `strcat`/`strcpy` in argv command construction and import parsing. `tool_newDefGroup` appears to pass the full `owner:group` string to `PDB_createGroup` but briefly truncates it only for owner lookup. Export mutates `rec.name` in memory when escaping colons. Error handling is mixed between printed failures and assertions in lower layers.
