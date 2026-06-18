# sources/distributed-fs/juicefs/pkg/object/azure.go

## Purpose
`azure.go` implements the `wasb` object storage backend for Azure Blob Storage.

## Important APIs, Types, and Functions
The `wasb` type embeds `DefaultObjectStorage` and `tierStorage` and holds Azure container/blob clients plus auth mode. It implements `String`, `Create`, `Head`, `Get`, `Put`, `Copy`, `Delete`, `List`, and `Restore`. Helper functions include `toValue`, `str2Tier`, `createAzureCredential`, `normalizeSASToken`, `domainFromHost`, `autoWasbEndpoint`, and `newWasb`.

## Control Flow and State
`newWasb` parses endpoint/container, then selects authentication in priority order: `AZURE_STORAGE_CONNECTION_STRING`, SAS token or managed identity when account key is absent, and shared key otherwise. It auto-detects public or China cloud endpoint suffixes when the host lacks a domain. `Put` applies storage tier and optional validated tag. `Copy` either changes tier/tags in place when tier context targets the same key, or performs server-side copy; shared-key copy uses a short-lived source SAS URL while token auth uses the direct source URL. `List` uses flat paging and rejects delimiter mode.

## State and Persistence Behavior
Persistent state is Azure containers and blobs. Local state records the container name, client handles, tier configuration, and whether token auth is in use. Deletes treat missing blobs as success. Azure archive restore is unsupported because Azure tier changes are permanent rather than temporary restore requests.

## Dependencies and Integration Points
It depends on Azure SDK `azblob`, `azcore`, `azidentity`, blob/container/SAS packages, AWS helper pointers for request ids, and JuiceFS object abstractions including `ObjectStorage`, `AttrGetter`, tiers, tags, and registration via `Register("wasb", newWasb)`.

## Risks and Test Signals
Risks include auth-mode confusion, SAS token handling with leading `?`, short SAS expiry during copy, delimiter listing unsupported by callers, nil response fields, endpoint auto-detection DNS failures, and missing request-id handling on errors. Tests should cover all auth priorities, public/China endpoint detection, tier/tag put and copy, missing-object mapping, ranged get, and list pagination.
