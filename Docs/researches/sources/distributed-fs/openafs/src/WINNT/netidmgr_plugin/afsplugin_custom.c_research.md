# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsplugin_custom.c

## Purpose
Implements an MSI custom action that strips registry-decoration prefixes from selected installer properties representing DWORD values.

## Important APIs, Types, And Functions
`dword_props` lists `OPENAFSVERSIONMAJOR`, `OPENAFSVERSIONMINOR`, and `KFWVERSIONMAJOR`. `strip_decoration()` removes a leading `#` in-place. `StripRegDecoration()` is exported/stdcall-style MSI custom action code that gets and sets properties through `MsiGetProperty()` and `MsiSetProperty()`.

## Control Flow
For each property, the custom action reads up to 16 TCHARs, strips a leading `#` when present, and writes the property back. It always returns `ERROR_SUCCESS`.

## State And Persistence
State is MSI session property data. The effect is transient within installer execution unless later installer tables consume and persist those property values.

## Dependencies And Integration Points
Depends on Windows Installer `msiquery.h`, TCHAR/UNICODE conventions, and installer sequencing that invokes `StripRegDecoration`.

## Risks
The function ignores read/set failures and reports success, which can hide malformed installer state. The 16-character buffer assumes DWORD string representations only.

## Test Signals
MSI custom-action tests should pass properties with and without `#`, missing properties, and boundary-length numeric strings.
