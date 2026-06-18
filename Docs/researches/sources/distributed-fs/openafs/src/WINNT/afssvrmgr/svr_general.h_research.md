# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_general.h

Purpose: Declares default warning constants and server preference/menu APIs.

Important APIs/types: Defines default aggregate-full and fileset-full warning percentages and service-stop warning default. Exports server popup helpers and preference load/save functions.

Control flow/state: Defaults are used by server/fileset property UIs when stored preferences are absent or disabled.

Dependencies/integration: Included by server property, fileset property, and tab modules.

Risks/test signals: Changing defaults affects first-run preferences and UI fallback values but may not migrate existing stored preferences.
