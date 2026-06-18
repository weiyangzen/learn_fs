# sources/distributed-fs/openafs/src/WINNT/client_config/cellservdb.c

## Purpose
`cellservdb.c` implements an editable in-memory model for OpenAFS `CellServDB`/`AFSDCELL.INI` style files. It reads file lines into a doubly linked list, parses cell and server records, formats records back into text, and supports add/remove operations used by the Hosts tab.

## Important APIs, Types, and Functions
Key exports are `CSDB_GetFileName`, `CSDB_ReadFile`, `CSDB_WriteFile`, `CSDB_FreeFile`, `CSDB_CrackLine`, `CSDB_FormatLine`, `CSDB_FindCell`, `CSDB_RemoveCell`, `CSDB_RemoveCellServers`, `CSDB_AddCell`, `CSDB_AddCellServer`, `CSDB_AddLine`, and `CSDB_RemoveLine`. It uses `CELLDBLINE`, `CELLSERVDB`, and `CELLDBLINEINFO`.

## Control Flow
`CSDB_ReadFile` resolves the path through `cm_GetCellServDB` when no filename is supplied, reads the full file, strips leading whitespace and blank lines, splits on EOLs, and appends each line into a linked list. `CSDB_CrackLine` distinguishes cell lines beginning with `>` from server-address lines, extracts optional linked cell/comment text, and converts server IP addresses with `inet_addr`. `CSDB_AddCell` creates or rewrites a cell line; server additions insert after a given line; remove helpers delete a cell header and/or following server lines until the next cell.

## State and Persistence Behavior
The `CELLSERVDB` object owns filename, dirty flag, and linked-list nodes. Writes only occur when `fChanged` is true and rewrite the whole file with CRLF endings. `CSDB_FreeFile` releases all nodes and clears the owner struct.

## Dependencies and Integration Points
The Hosts tab uses this module to display, edit, validate, and persist cell/server entries. `tab_general.cpp` also uses `CSDB_FindCell` as one fallback during cell validation. The file depends on OpenAFS `cm_config.h` for locating CellServDB and Winsock for IP parsing.

## Risks and Edge Cases
The parser drops blank/comment-only lines because it skips leading whitespace/eol and only stores parsed non-empty text, so a write may not preserve original formatting/comments. `CSDB_AddLine` uses `strcpy` into fixed `cchCELLDBLINE` buffers and assumes callers format bounded lines. One pointer bug appears in insertion: assigning `pNew->pNext->pPrev = pNew->pPrev` should likely be `pNew`, otherwise inserting in the middle can corrupt backward links.

## Test Signals
Tests should read/write a representative CellServDB with cells, linked cells, server comments, invalid IP lines, and multiline edits. Linked-list integrity after middle insert/remove, dirty-flag behavior, and preservation or intentional loss of comments should be verified.
