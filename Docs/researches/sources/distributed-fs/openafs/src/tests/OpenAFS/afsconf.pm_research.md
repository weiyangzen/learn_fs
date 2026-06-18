# sources/distributed-fs/openafs/src/tests/OpenAFS/afsconf.pm

## Purpose
`afsconf.pm` is a Perl AFStools-derived module that reads local AFS configuration files and exposes the local cell, canonical cell names, cell servers, known cells, and cache configuration.

## Important APIs, types, and functions
Package `OpenAFS::afsconf` exports `AFS_conf_localcell`, `AFS_conf_canoncell`, `AFS_conf_listcells`, `AFS_conf_cellservers`, and `AFS_conf_cacheinfo`. Internal `_confpath` locates configuration files and `_findcell` parses `CellServDB`.

## Control flow
`_confpath` checks a cached `%conf_paths`, a configured `confdir`, and a default config directory. `AFS_conf_localcell` reads the first line of `ThisCell`. `_findcell` escapes the requested prefix, scans `CellServDB` for a unique matching `>` cell stanza, optionally collects server hostnames/IPs while in that stanza, caches canonical names, and dies on ambiguity or absence. `AFS_conf_listcells` scans every `>` stanza. `AFS_conf_cacheinfo` parses `cacheinfo` colon fields and translator host from `AFSSERVER`, `$HOME/.AFSSERVER`, or `/.AFSSERVER`.

## State and persistence behavior
It reads config files and environment variables, and caches configuration paths and canonical cell names in package globals inherited from the broader AFStools config/util environment. It does not write files.

## Dependencies and integration points
It depends on `OpenAFS::CMU_copyright`, `OpenAFS::config`, `OpenAFS::util`, `%AFS_Parms`, `%AFS_Help`, `%conf_paths`, `$def_ConfDir`, and standard OpenAFS config file formats.

## Risks
Prefix matching for cell names can be ambiguous. `CellServDB` parsing is old and primarily recognizes dotted numeric server entries, so modern hostname/comment variants may not parse as intended. `_confpath` dies when files are absent, while some callers expect optional behavior. Translator lookup relies on `$ENV{HOME}`.

## Test signals
Use fixture config directories for `ThisCell`, `CellServDB`, and `cacheinfo`; test canonical prefix success, ambiguous prefix failure, missing files, server list parsing, cell listing, cache hard limit parsing, and translator environment/file precedence.
