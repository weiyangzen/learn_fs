# sources/distributed-fs/openafs/src/kauth/client.c

Purpose: provides common kauth client utilities for password-to-key conversion, secure password reading, login-name parsing, and one-time client initialization.

Important APIs and functions: `ka_StringToKey`, `ka_ReadPassword`, `ka_ParseLoginName`, and `ka_Init`. Internal helpers are `Andrew_StringToKey`, Kerberos-style `StringToKey`, and `map_char`.

Control flow and state: `ka_StringToKey` maps a cell to a realm, lowercases for backward compatibility, and uses Andrew string-to-key for passwords of 8 characters or fewer, otherwise the DES CBC checksum-based string-to-key. `ka_ReadPassword` reads without echo and optionally verifies, rejects empty passwords, then derives a key. `ka_ParseLoginName` parses `name.instance@cell` with backslash quoting and three-digit octal escapes, uppercases the cell/realm, and bounds checks each component. `ka_Init` initializes error tables once and opens client cell configuration.

Dependencies and integration: uses hcrypto DES/UI helpers, `crypt`, pthread global lock macros, cellconfig/auth utilities, rxkad conversion helpers, and kauth error tables. Used by auth clients, admin tools, and command-line programs.

Risks: password handling is legacy DES-based and uses fixed buffers; `strncpy(password, str, sizeof(password))` may not NUL-terminate before `strlen` if input is oversized; backslash-octal parsing assumes enough following characters. Test signals should cover quoted login names, missing output parameters, component length limits, cell uppercasing, empty password rejection, short versus long password key derivation, and repeated `ka_Init`.
