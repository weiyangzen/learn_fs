<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/config.cpp -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/config.cpp

## Purpose
`config.cpp` provides Windows winutils helpers for locating configuration files relative to the running module and reading a single Hadoop XML configuration value by property name using MSXML6.

## Important APIs, Types, And Functions
`BuildPathRelativeToModule(relativePath, len, buffer)` builds an absolute path from the executable's drive and directory plus a caller-supplied relative path. `GetConfigValue(relativePath, keyName, len, value)` resolves the XML path relative to the module and delegates to `GetConfigValueFromXmlFile`. `GetConfigValueFromXmlFile(xmlFile, keyName, outLen, outValue)` initializes COM, loads an MSXML DOM document, builds an XPath of the form `//configuration/property[name='KEY']/value/text()`, selects the first matching value node, allocates a wide string with `LocalAlloc`, copies the BSTR content, and returns length plus caller-owned value. The `ERROR_CHECK_HRESULT_DONE` macro logs and exits on HRESULT failures.

## Control Flow
The relative-path helper calls `GetModuleFileName`, splits drive/path with `_wsplitpath_s`, then formats the final path with `StringCbPrintf`. The config getter initializes outputs to empty, resolves the full path, and logs when a value is found. The XML parser calls `CoInitialize`, creates `MSXML2::DOMDocument60`, disables async validation and external resolution, loads the XML file, selects the XPath, copies the value if present, catches `_com_error`, and calls `CoUninitialize` if COM was initialized.

## State And Persistence Behavior
The module has no persistent state. It allocates returned configuration values with `LocalAlloc`; callers must free them with `LocalFree`. COM initialization is per-call. It reads but does not modify XML. When a key is absent, it returns `ERROR_SUCCESS` with `*outLen == 0` and `*outValue == NULL`.

## Dependencies And Integration Points
Dependencies include `winutils.h`, Windows path/string APIs, COM, and `#import "msxml6.dll"` for MSXML smart pointers. It is used by Windows service or utility code that needs Hadoop XML settings from files deployed next to the executable. It assumes Hadoop XML uses the standard `<configuration><property><name>...` layout also used by `core-default.xml` and site files.

## Risks
`BuildPathRelativeToModule` treats any nonzero `GetLastError()` after `GetModuleFileName` as failure even though `GetLastError` is not reliable on success unless the return value indicates truncation; stale last-error state could cause false failures. The XPath directly interpolates `keyName`, so property names containing XPath quote/control syntax could break selection; Hadoop property names are normally safe. `StringCbPrintf` receives a character count from callers but expects bytes, so buffer-size semantics are inconsistent in `BuildPathRelativeToModule`; the current `MAX_PATH` use leaves room, but future callers could understate/overstate capacity. XML external resolution is disabled, reducing XXE risk, but parsing arbitrary XML still depends on MSXML behavior. The function only returns the first matching property value.

## Test Signals
Tests should cover module-relative path construction, absent keys, empty values, duplicate keys, malformed XML, missing XML files, property names with punctuation, Unicode values, COM initialization failures, and caller freeing. Static analysis should flag the `GetLastError` success-path assumption and byte-vs-character size mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/config.cpp -->
