# sources/compression/zlib/contrib/dotzlib/DotZLib/AssemblyInfo.cs

Purpose: .NET assembly metadata for the DotZLib bindings project.

Important attributes: `AssemblyTitle("DotZLib")`, description for “.Net bindings for ZLib compression dll 1.2.x”, company/copyright metadata, `AssemblyVersion("1.0.*")`, and strong-name attributes `AssemblyDelaySign(false)`, empty `AssemblyKeyFile`, and empty `AssemblyKeyName`.

Control flow: declarative assembly attributes only; compiled into the .NET assembly.

State and persistence: affects assembly identity, generated version, and signing metadata. No runtime state.

Dependencies and integration: uses `System.Reflection` and `System.Runtime.CompilerServices`; consumed by legacy .NET project files in DotZLib.

Risks: wildcard assembly version creates build-dependent identities, which can complicate reproducible builds and binding redirects. Description references zlib 1.2.x and may be stale relative to current zlib sources.

Test signals: compile success of DotZLib validates metadata syntax; no functional tests are present in this file.
