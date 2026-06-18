# File Research: sources/block-storage/cryptsetup/src/utils_key_description.c

## Purpose
Helpers for parsing kernel keyring key descriptions used for volume-key retrieval and volume-key linking.

## Volume Key Description
`tools_parse_vk_description()` applies a default `%user:` key type prefix when the user-supplied key description does not start with `%`; otherwise it duplicates the supplied typed description.

## Link Description Parsing
`parse_single_vk_and_keyring_description()` parses `--link-vk-to-keyring` values in the form:
`<keyring>::[%<type>:]<key-description>`

It:
- Splits keyring and key description on `::`.
- Extracts optional key type from the key part.
- Ignores an explicit type on the keyring part with a verbose warning.
- Accepts numeric/keyring-special values directly or prefixes normal keyring names with `%:`.
- Duplicates parsed keyring, key, and optional type output parts.

## Multi-Key Linking
`tools_parse_vk_and_keyring_description()` parses up to two link descriptions, ensures both volume keys use the same key type and same keyring, then calls `crypt_set_keyring_to_link()`.

## Error Handling
Invalid syntax returns `-EINVAL` and logs an invalid value message. `-EAGAIN` from libcryptsetup is converted into a “supply more key names” diagnostic.

## Notes
The `cd` parameter is required for the final libcryptsetup keyring-link setup, not for the string parsing itself.
