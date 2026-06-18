# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/hdfs/explorer.js

## Purpose

`explorer.js` implements the HDFS file browser in the NameNode web UI. It navigates directories through WebHDFS, renders file listings, opens file/block details, previews file heads/tails, and exposes mutating operations such as delete, chmod, owner/group/replication edits, mkdir, upload, and move via cut/paste.

## Important APIs and functions

- `browse_directory(dir)` calls `/webhdfs/v1/<path>?op=LISTSTATUS`, renders the explorer table, wires row actions, and initializes DataTables.
- `view_file_details(path, abs_path)` calls `GET_BLOCK_LOCATIONS`, renders block-location details, sets a WebHDFS `OPEN` download URL, and previews head/tail chunks using `noredirect=true`.
- `makeEditable(elementType, op, parameter)` connects X-editable fields to WebHDFS `SETOWNER` and `SETREPLICATION` operations.
- `view_perm_details()` and `set_permissions()` render a Bootstrap popover for octal permission bits and submit `SETPERMISSION`.
- `delete_path()` opens a Bootstrap confirmation modal and submits recursive `DELETE`.
- `encode_path()` percent-encodes paths while preserving `/` separators for WebHDFS URL layout.
- Upload and directory creation handlers submit WebHDFS `CREATE` and `MKDIRS`; cut/paste uses `sessionStorage` plus WebHDFS `RENAME`.

## Control flow

Initialization compiles explorer and block-info templates, wires navigation controls, and browses the URL hash path or `/`. Directory browsing updates `current_directory`, the location hash, and the directory input, then binds all action handlers after template render. File clicks either recurse into `browse_directory` for directories or open `view_file_details` for files.

Mutations generally submit a WebHDFS request, refresh the current directory on success, and show the shared alert panel on failure. Upload is two-step WebHDFS create: first request the DataNode redirect location with `noredirect=true`, then PUT bytes to the returned `Location`.

## State and persistence behavior

`current_directory` is in-memory page state and the active path is mirrored to `window.location.hash`. Cut/paste state is persisted in `sessionStorage` under `source_directory` and `selected_file_names`, surviving page reloads within the browser session. The file preview keeps one local `request` variable per modal setup and aborts a previous preview request before starting another. No server-side state is cached by this script beyond HDFS mutations.

## Dependencies and integration points

The file depends on jQuery, Dust, Moment, DataTables, Bootstrap modals/popovers/buttons, X-editable, `JSONParseBigNum`, WebHDFS, `/conf`, and templates in the HDFS explorer page. It is the main consumer of `bootstrap-editable.min.js` in this set through `.editable()`.

## Risks and edge cases

- Several user-facing strings are written with `.html()` or concatenated into URLs/HTML; correctness depends on trusted server values and template escaping.
- Head/tail preview uses synchronous Ajax (`async: false`) and can block the browser.
- Directory creation computes permissions as `777 - umask`, which treats string values as decimal arithmetic and may be surprising for octal permissions.
- Cut/paste assumes valid JSON in `sessionStorage`; missing or stale selected files can throw or submit unexpected rename requests.
- Upload completion refreshes after all second-stage PUTs settle, but errors can reset the modal before remaining uploads finish.
- Mutating operations are exposed directly from the browser and rely on WebHDFS authentication/authorization for safety.

## Test signals

Strong tests would mock WebHDFS for list, block locations, delete, set permission, set owner/group, set replication, mkdir, create/upload redirects, and rename. Browser tests should cover hash navigation, root parent disabling, permission bit mapping, DataTables rendering, preview failure paths, selected-file storage, upload multi-file completion, and status-specific error messages for 401, 403, 404, and generic failures.
