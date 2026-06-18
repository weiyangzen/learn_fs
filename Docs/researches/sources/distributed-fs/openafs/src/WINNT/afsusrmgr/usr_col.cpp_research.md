# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_col.cpp

Purpose: supplies default user-list view settings and converts cached user object properties into displayable column values for FastList/list views.

Important APIs and control flow: `User_SetDefaultView` initializes `VIEWINFO` with all user columns, default sort by name, five visible columns, and status icon view. `User_GetColumn` calls `asc_ObjectPropertiesGet_Fast`, switches over `USERCOLUMN`, formats text/date/elapsed/numeric values from KAS and PTS fields, and sets `COLUMNTYPE` for sorting. `User_GetDisplayName` formats user name plus instance except for special `admin` and `krbtgt` entries; the ASID overload falls back to `asc_ObjectNameGet_Fast`. `User_SplitDisplayName` splits dotted names into name/instance except machine accounts.

State and dependencies: this module reads cached admin-server object properties through global `g.idClient`/`g.idCell` and uses UI formatting helpers (`GetString`, `FormatTime`, `FormatElapsedSeconds`, `FormatServerKey` indirectly via dependencies). It does not own durable state.

Risks and test signals: column formatting assumes buffers are large enough for `wsprintf` and string concatenation. Display-name parsing must preserve machine account names and hide only the intended special instances. Test signals include column sort type correctness, mixed KAS/PTS availability, expiration and lifetime formatting, and dotted principal handling.
