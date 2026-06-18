## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/PathsModel.hh

Purpose: represents a list of paths for archiveinfo, release, and stage cancellation operations.

Important APIs/types/functions: `addFile(path)` and `getFiles`.

Control flow: `PathsModelBuilder` populates it from JSON; business methods consume its `FilesContainer`.

State and persistence: in-memory path list only.

Dependencies and integration points: uses `FilesContainer`, so paths are duplicate-slash-normalized.

Risks and test signals: tests should cover accepted JSON shapes, path normalization, empty lists, duplicate paths, and cancellation paths not in request.
