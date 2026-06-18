<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/resource.h

Purpose: Central numeric resource ID header for the server configuration UI.

Important APIs/definitions: Defines string IDs (`IDS_*`) for wizard text, configuration step messages, validation/error messages, service/partition labels, salvage text, and warnings. Defines icon/bitmap/dialog IDs (`IDI_*`, `IDB_*`, `IDD_*`) and control IDs (`IDC_*`, `IDNEXT`, `IDBACK`) used by all dialog procedures and help mappings.

Control flow: No runtime logic. The IDs bind C++ dialog code to localized `.rc` resources and help context tables.

State and persistence: None.

Dependencies and integration points: Included by nearly every `afssvrcfg` source file. Must stay synchronized with `lang/*/afscfg.rc`, help registration in `help.cpp`, and dialog procedures.

Risks: Duplicate control IDs exist intentionally or accidentally (`IDC_FS_STATUS_MSG` and `IDC_SCS_PROMPT`, `IDC_SCS_FRAME` and `IDC_HOSTNAME_FRAME` share values), so code must only use them in the correct dialog template. Numeric gaps and frozen string catalog comments make adding messages delicate. Resource mismatch causes runtime UI/help failures rather than compile errors.

Test signals: Resource compile, open every dialog, verify every referenced ID exists in each template, check localized string coverage, and validate help mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/resource.h -->
