## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_create.cpp

Purpose: implements machine-account creation dialog using user creation task infrastructure with KAS disabled and PTS enabled.

Important APIs/types/functions: `Machine_SetDefaultCreateParams`, `Machine_ShowCreate`, `Machine_Create_DlgProc`, `Machine_Create_OnInitDialog`, `Machine_Create_OnNames`, `Machine_Create_OnID`, `Machine_Create_OnAdvanced`, `Machine_Create_OnOK`, and `Machine_Create_OnEndTask_ObjectGet`.

Control flow: initialization formats title with current cell, creates a positive UID spinner, selects auto-ID, and fetches cell max user ID with `taskOBJECT_GET`. Name changes enable OK and disable manual ID for multiple names. Advanced opens user properties in machine mode. OK builds `USER_CREATE_PARAMS` with blank password, PTS-only creation, machine defaults, membership/owned group lists, and tokenized machine names, then starts `taskUSER_CREATE`.

State and persistence behavior: default machine creation properties are initialized on first run and saved back to `gr.CreateMachine` after OK. Temporary advanced ASID lists are freed after dialog close.

Dependencies and integration points: reuses `usr_prop` and user-create task structures, spinner helpers, localized separators, `FormatMultiString`, and OpenAFS cell max UID properties.

Risks: machine-account validity is not visibly enforced here; names are merely tokenized. KAS fields are forced false/zero, so future machine-auth changes need explicit updates. Multiple names force auto IDs.

Test signals: create one machine with auto/manual UID, multiple machines, advanced membership/quota changes, cancel advanced edits, and verify task parameters set `fCreateKAS = FALSE` and `fCreatePTS = TRUE`.
