## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_col.cpp

Purpose: defines default group-list column layout and values for lazy FastList display and sorting.

Important APIs/types/functions: `Group_SetDefaultView` initializes `VIEWINFO` with all group columns and default shown columns; `Group_GetColumn` maps `GROUPCOLUMN` values to text or `COLUMNTYPE`.

Control flow: default view starts in small-icon mode, exposes name, UID, and member count, and uses status icon view. `Group_GetColumn` retrieves `ASOBJPROP` through `asc_ObjectPropertiesGet_Fast`, then formats name, member count, UID, owner, or creator with numeric IDs when names are unavailable.

State and persistence behavior: no persistence itself; writes defaults into `gr.viewGrp` and `gr.ivGrp` during first-run initialization. Runtime column ordering is later persisted by settings storage.

Dependencies and integration points: used by `display.cpp`, `general.cpp` sorting, and startup defaults. Depends on `GROUPCOLUMNS` from `grp_col.h`, localized string IDs, and OpenAFS cached group properties.

Risks: formatting uses caller-provided buffers and `wsprintf`. Owner/creator output is alphabetic even when it falls back to numeric ID, which may surprise sort behavior.

Test signals: display and sort every group column with full properties, missing names, and large member/UID values; verify default first-run column choices.
